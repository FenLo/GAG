const { SlashCommandBuilder, PermissionFlagsBits } = require('discord.js');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('purge')
        .setDescription('Belirli sayıda mesajı topluca siler.')
        .addIntegerOption(option =>
            option.setName('amount')
                .setDescription('Silinecek mesaj sayısı (1-100 arası)')
                .setRequired(true)
                .setMinValue(1)
                .setMaxValue(100))
        .setDefaultMemberPermissions(PermissionFlagsBits.ManageMessages),
    async execute(interaction) {
        const amount = interaction.options.getInteger('amount');

        try {
            const messages = await interaction.channel.messages.fetch({ limit: amount });
            await interaction.channel.bulkDelete(messages, true);
            
            const reply = await interaction.reply({ 
                content: `🗑️ ${messages.size} mesaj silindi.`,
                fetchReply: true 
            });
            
            setTimeout(() => reply.delete().catch(() => {}), 5000);
        } catch (error) {
            console.error('Purge error:', error);
            await interaction.reply({ 
                content: '❌ Mesajları silerken bir hata oluştu.',
                ephemeral: true 
            });
        }
    }
};
