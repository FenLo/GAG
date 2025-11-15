const { SlashCommandBuilder, PermissionFlagsBits } = require('discord.js');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('crypto')
        .setDescription('Kripto embedlerinin gönderileceği kanalı seçer ve kaydeder.')
        .addChannelOption(option =>
            option.setName('kanal')
                .setDescription('Embed mesajların gönderileceği kanal')
                .setRequired(true))
        .setDefaultMemberPermissions(PermissionFlagsBits.Administrator),
    async execute(interaction) {
        const channel = interaction.options.getChannel('kanal');

        // TODO: Implement crypto channel storage and periodic updates
        
        await interaction.reply({
            content: `💰 Kripto verileri özelliği henüz geliştirilme aşamasındadır. Kanal: ${channel}`,
            ephemeral: true
        });
    }
};
