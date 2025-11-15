const { SlashCommandBuilder } = require('discord.js');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('gayrate')
        .setDescription('Belirtilen kişinin gay oranını ölçer.')
        .addUserOption(option =>
            option.setName('name')
                .setDescription('Kullanıcı')
                .setRequired(true)),
    async execute(interaction) {
        const user = interaction.options.getUser('name');
        const gayPercentage = Math.floor(Math.random() * 101);
        
        await interaction.reply(`🏳️‍🌈 ${user} **${gayPercentage}%** gay! 🏳️‍🌈`);
    }
};
